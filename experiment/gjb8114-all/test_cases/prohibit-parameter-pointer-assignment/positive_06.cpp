struct Counter
{
    int value;

    int get() const
    {
        return value;
    }
};

int read_counter(Counter* counter)
{
    if (counter != nullptr)
    {
        return counter->get();
    }
    return 0;
}

int main()
{
    Counter c{42};
    return read_counter(&c);
}
