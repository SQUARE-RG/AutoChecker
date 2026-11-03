int compute(int value) {
    auto multiply = [](int x) {
        int result = x * 2;
        return result;
    };
    return multiply(value);
}

int main() {
    return compute(3);
}
