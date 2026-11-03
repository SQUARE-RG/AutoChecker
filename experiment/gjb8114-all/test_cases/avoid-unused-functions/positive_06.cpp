int main() {
    struct LocalReporter {
        int compute() const {
            return 2;
        }
    };

    LocalReporter reporter;
    return reporter.compute();
}
