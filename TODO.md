- Fix random sampling
- Add CLI to analyze.py
- Move everything to object oriented code
- Full mypy coverage
- Pytest coverage
- Testing for all functionality
- Comments everywhere
- Library separation

class MetricsCalculator:

    def average(self) -> float()

class CLILineCreator:

    def average() -> str:
        my_average = self._metrics_calculator.average()
        return f'Average is {my_average}'
    
class CliPrinter:
    def average():
        cli_line_creator = CLILineCreator()
        line = cli_line_creator.average()
        print(line)
    
