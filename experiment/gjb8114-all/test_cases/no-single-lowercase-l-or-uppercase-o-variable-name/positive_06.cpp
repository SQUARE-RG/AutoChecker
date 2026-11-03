int main() {
    auto addOne = [](int number) -> int {
        int sum = number + 1;
        return sum;
    };
    return addOne(1);
}
