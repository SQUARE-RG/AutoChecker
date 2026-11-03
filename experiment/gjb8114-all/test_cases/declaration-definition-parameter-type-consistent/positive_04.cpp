int apply_twice(int (*func)(int), int value);

int increment(int x)
{
    return x + 1;
}

int apply_twice(int (*func)(int), int value)
{
    return func(func(value));
}

int main()
{
    return apply_twice(increment, 3);
}
