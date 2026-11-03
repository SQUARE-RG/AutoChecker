int main()
{
    auto sum = [](int value) {
        int arr[3]{value, value + 1, value + 2};
        return arr[0] + arr[1] + arr[2];
    };
    return sum(1) - 6;
}
