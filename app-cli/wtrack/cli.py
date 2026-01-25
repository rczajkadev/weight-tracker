from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.style import Style
from rich.table import Table

from . import api_client as api
from . import auth
from .constants import APP_NAME, WEIGHT_UNIT
from .errors import AppError
from .visualizer import plot_data

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .models import WeightEntry, WeightStats

SPINNER = 'arc'
ADHERENCE_WINDOWS = {30}
DATE_FORMAT = '%Y-%m-%d'
DATE_FORMAT_LABEL = 'YYYY-MM-DD'

STATUS_STYLE = Style(color='bright_cyan', bold=True)
STATUS_OK = '[bold bright_cyan]OK[/]'
STATUS_NO = '[bold deep_pink2]NO[/]'

app = typer.Typer(name=APP_NAME, add_completion=False, no_args_is_help=True)

console = Console(width=120)


@app.command('login', help='aliases: signin')
@app.command('signin', hidden=True)
def login() -> None:
    ok, _ = _run_with_status('Signing in...', auth.acquire_token)

    if not ok:
        return

    console.print('\nSigned in.\n')


@app.command('logout', help='aliases: signout')
@app.command('signout', hidden=True)
def logout() -> None:
    auth.logout()
    console.print('\nSigned out.\n')


@app.command('status', help='aliases: streak')
@app.command('streak', hidden=True)
def show_status() -> None:
    ok, status = _run_with_token('Checking status...', api.get_status)

    if not ok or status is None:
        return

    console.print()

    if status.today.has_entry:
        current_weight = f'{status.today.weight} {WEIGHT_UNIT}'
        console.print(f'{STATUS_OK} Data added: [bold bright_cyan]{current_weight}[/]')
    else:
        console.print(f'{STATUS_NO} No entry yet today.')

    console.print()

    current_streak = _format_days(status.streak.current)
    longest_streak = _format_days(status.streak.longest)

    console.print(
        f'[bold]Streak:[/] [bold bright_cyan]{current_streak}[/] (best: [bold bright_cyan]{longest_streak}[/])'
    )

    for adherence in status.adherence:
        window = adherence.window

        if window not in ADHERENCE_WINDOWS:
            continue

        days_missed = adherence.days_missed
        console.print(f'[bold]Adherence ({window}d):[/] [bold bright_cyan]{days_missed}[/] missed')

    console.print()


@app.command('add', help='aliases: new, insert')
@app.command('new', hidden=True)
@app.command('insert', hidden=True)
def add_weight_data(
    weight: Annotated[float, typer.Argument(help='Weight value')],
    date: Annotated[str | None, typer.Option('-d', '--date', help=f'Date in {DATE_FORMAT_LABEL} format')] = None,
) -> None:
    weight = _validate_weight(weight)

    if date is not None:
        date = _validate_date(date, 'Date')

    ok, _ = _run_with_token('Adding data...', lambda token: api.add_weight_data(date, weight, token))

    if not ok:
        return

    console.print('\nData added successfully.\n')


@app.command('report', help='aliases: show, get, list, ls, display')
@app.command('show', hidden=True)
@app.command('get', hidden=True)
@app.command('list', hidden=True)
@app.command('ls', hidden=True)
@app.command('display', hidden=True)
def show_report(
    date: Annotated[str | None, typer.Argument(help=f'Specific date in {DATE_FORMAT_LABEL} format')] = None,
    date_from: Annotated[
        str | None, typer.Option('--date-from', help=f'Start date in {DATE_FORMAT_LABEL} format')
    ] = None,
    date_to: Annotated[str | None, typer.Option('--date-to', help=f'End date in {DATE_FORMAT_LABEL} format')] = None,
    tail: Annotated[int, typer.Option('--tail', help='Show only last N records in table')] = 7,
    plot: Annotated[bool, typer.Option('--plot', help='Display chart in browser')] = False,
) -> None:
    if date and (date_from or date_to):
        raise typer.BadParameter('Use either a specific date or --date-from/--date-to.')

    if date:
        date = _validate_date(date, 'Date')
        _handle_report_for_specific_day(date)
        return

    tail = max(0, tail)

    if date_from is not None:
        date_from = _validate_date(date_from, 'Date from')
    if date_to is not None:
        date_to = _validate_date(date_to, 'Date to')
    if date_from and date_to and _parse_date(date_from, 'Date from') > _parse_date(date_to, 'Date to'):
        raise typer.BadParameter('Date from must be before or equal to date to.')

    ok, report = _run_with_token('Fetching data...', lambda token: api.get_weight_data(date_from, date_to, token))

    if not ok or report is None:
        return

    if not report.data:
        console.print('No data found.')
        return

    sorted_entries = _sort_entries(report.data)
    avg_value = report.stats.avg if report.stats else 0.0

    table = _create_weight_data_table(sorted_entries, tail)

    console.print()
    console.print(f'Weight unit: [bold bright_cyan]{WEIGHT_UNIT}[/]')
    console.print()
    console.print(table)

    console.print()
    console.print(f'Displayed: {min(len(sorted_entries), tail)}')
    console.print(f'Total received: {len(sorted_entries)}')
    console.print()

    _print_date_range(sorted_entries)
    _print_weight_stats(report.stats)

    today_weight = _find_today_weight(sorted_entries)

    if today_weight is not None and report.stats is not None:
        _print_current_weight(today_weight, float(avg_value))

    if plot:
        _run_with_status('Plotting data...', lambda: plot_data(sorted_entries, float(avg_value)))


@app.command('update', help='aliases: edit')
@app.command('edit', hidden=True)
def update_weight_data(
    weight: Annotated[float, typer.Argument(help='Weight value')],
    date: Annotated[str, typer.Option('-d', '--date', help=f'Date in {DATE_FORMAT_LABEL} format')],
) -> None:
    weight = _validate_weight(weight)
    date = _validate_date(date, 'Date')

    ok, _ = _run_with_token('Updating data...', lambda token: api.update_weight_data(date, weight, token))

    if not ok:
        return

    console.print('\nData updated.\n')


@app.command('remove', help='aliases: rm, delete')
@app.command('rm', hidden=True)
@app.command('delete', hidden=True)
def remove_weight_data(
    date: Annotated[str, typer.Argument(help=f'Date in {DATE_FORMAT_LABEL} format')],
) -> None:
    date = _validate_date(date, 'Date')

    console.print(f'\nAre you sure you want to remove data for [bold bright_cyan]{date}[/]?', end='')

    if not typer.confirm(''):
        console.print('Operation cancelled.')
        return

    ok, _ = _run_with_token('Removing data...', lambda token: api.delete_weight_data(date, token))

    if not ok:
        return

    console.print('Data removed.\n')


def _run_with_status[T](message: str, action: Callable[[], T]) -> tuple[bool, T | None]:
    try:
        with console.status(message, spinner=SPINNER, spinner_style=STATUS_STYLE):
            return True, action()
    except AppError as exc:
        _print_error(exc)
        return False, None


def _run_with_token[T](message: str, action: Callable[[str], T]) -> tuple[bool, T | None]:
    def _call() -> T:
        token = auth.acquire_token()
        return action(token)

    return _run_with_status(message, _call)


def _print_error(error: AppError) -> None:
    console.print(f'[bold red]Error:[/] {error.message}')


def _format_days(days: int) -> str:
    unit = 'day' if days == 1 else 'days'
    return f'{days} {unit}'


def _parse_date(value: str, label: str) -> date:
    try:
        return datetime.strptime(value, DATE_FORMAT).date()
    except ValueError as exc:
        raise typer.BadParameter(f'{label} must be in {DATE_FORMAT_LABEL} format.') from exc


def _validate_date(value: str, label: str) -> str:
    _parse_date(value, label)
    return value


def _validate_weight(weight: float) -> float:
    if weight <= 0:
        raise typer.BadParameter('Weight must be a positive number.')
    return weight


def _sort_entries(entries: Sequence[WeightEntry]) -> tuple[WeightEntry, ...]:
    def sort_key(entry: WeightEntry) -> tuple[int, date | str]:
        try:
            return (0, _parse_date(entry.date, 'date'))
        except typer.BadParameter:
            return (1, entry.date)

    return tuple(sorted(entries, key=sort_key))


def _handle_report_for_specific_day(date: str) -> None:
    ok, response = _run_with_token('Fetching data...', lambda token: api.get_weight_data_by_date(date, token))

    if not ok or response is None:
        return

    display_date = response.date or date
    console.print(f'\nDate: [bold bright_cyan]{display_date}[/]')
    console.print(f'Weight: [bold bright_cyan]{response.weight} {WEIGHT_UNIT}[/]\n')


def _create_weight_data_table(weight_data: Sequence[WeightEntry], tail: int) -> Table:
    table = Table()

    table.add_column('Date', justify='center')
    table.add_column('Weight', justify='right')
    table.add_column('+/-', justify='right')

    if tail < 1:
        return table

    data_chunk = weight_data[-(tail + 1) :]
    skip_first_row = len(weight_data) > tail

    for index, item in enumerate(data_chunk):
        if index == 0 and skip_first_row:
            continue

        previous_weight = data_chunk[index - 1].weight if index > 0 else item.weight
        diff = item.weight - previous_weight
        diff_text = f'{diff:+.2f}'
        row_style = Style(bold=True) if diff > 0 else None

        table.add_row(item.date, f'{item.weight:.2f}', diff_text, style=row_style)

    return table


def _print_weight_stats(stats: WeightStats | None) -> None:
    if stats is None:
        console.print('Stats unavailable.\n')
        return

    console.print(f'Max: [bold bright_cyan]{stats.max:>6.2f} {WEIGHT_UNIT}[/]')
    console.print(f'Min: [bold bright_cyan]{stats.min:>6.2f} {WEIGHT_UNIT}[/]')
    console.print(f'Avg: [bold bright_cyan]{stats.avg:>6.2f} {WEIGHT_UNIT}[/]\n')


def _print_current_weight(weight: float, avg_value: float) -> None:
    if weight < avg_value:
        comparison = '[bold]LOWER[/] than'
    elif weight > avg_value:
        comparison = '[bold]HIGHER[/] than'
    else:
        comparison = '[bold bright_cyan]EQUAL[/] to'

    console.print(f'Current weight [bold bright_cyan]{weight:.2f} {WEIGHT_UNIT}[/] is {comparison} average.\n')


def _find_today_weight(weight_data: Sequence[WeightEntry]) -> float | None:
    today_value = datetime.utcnow().date().strftime(DATE_FORMAT)
    for entry in weight_data:
        if entry.date == today_value:
            return entry.weight
    return None


def _print_date_range(weight_data: Sequence[WeightEntry]) -> None:
    min_date = weight_data[0].date
    max_date = weight_data[-1].date

    console.print(f'Date range: [bold bright_cyan]{min_date}[/] - [bold bright_cyan]{max_date}[/]\n')
