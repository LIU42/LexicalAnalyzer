from analyzer import LexicalAnalyzer


def lexical_analysis(analyzer, source_path, output_path):
    with open(source_path, 'r') as sources:
        tokens, errors = analyzer.analysis(sources.readlines())

    with open(output_path, 'w') as outputs:
        if len(errors) == 0:
            outputs.writelines(f'{token}\n' for token in tokens)
        else:
            outputs.writelines(f'{error}\n' for error in errors)


def main():
    analyzer = LexicalAnalyzer()
    lexical_analysis(analyzer, 'samples/sample1.txt', 'outputs/output1.txt')
    lexical_analysis(analyzer, 'samples/sample2.txt', 'outputs/output2.txt')
    lexical_analysis(analyzer, 'samples/sample3.txt', 'outputs/output3.txt')
    lexical_analysis(analyzer, 'samples/sample4.txt', 'outputs/output4.txt')
    lexical_analysis(analyzer, 'samples/sample5.txt', 'outputs/output5.txt')


if __name__ == '__main__':
    main()
