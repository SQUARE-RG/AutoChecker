typedef int TData;

int apply(int value)
{
    auto worker = [](TData item) { return item + 1; };
    return worker(value);
}

int main()
{
    return apply(1);
}
