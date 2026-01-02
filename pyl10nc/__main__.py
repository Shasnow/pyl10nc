from . import generate
import argparse



def main():
    """Command-line entry point."""
    parser = argparse.ArgumentParser(description='Generate localization code from TOML file.')
    parser.add_argument('input', type=str, help='Path to the input TOML file.')
    parser.add_argument('--output', '-o', type=str, nargs='?', default=None,
                        help='Path to the output Python file (default: same as input with .py suffix).')

    args = parser.parse_args()

    try:
        generate(args.input, args.output)
    except Exception as e:
        print(f"❌ Code generation failed: {e}")
        exit(1)

if __name__ == '__main__':
    main()
