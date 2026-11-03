int limit = 10;

int main()
{
    limit = 5;
    auto fn = [](int value) {
        int result = value * 2;
        return result;
    };
    fn(3);
    return 0;
}
