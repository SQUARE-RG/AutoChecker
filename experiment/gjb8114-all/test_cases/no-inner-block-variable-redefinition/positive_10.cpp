int main() {
    int result = 1;
    auto compute = []() {
        int doubled = 5;
        return doubled;
    };
    result = compute();
    return result - 5;
}
