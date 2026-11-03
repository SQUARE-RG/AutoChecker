int main() {
    struct Local {
        int compute(int value) {
            return value + 1;
        }
    };

    Local local;
    return local.compute(41);
}
