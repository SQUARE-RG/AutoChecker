void helper()
{
}

int main()
{
    auto run = []() {
        int local_value = 0;
        return local_value;
    };
    return run();
}
