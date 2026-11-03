struct Counter
{
    static int value;
};

int Counter::value = 0;

int main()
{
    Counter::value = Counter::value + 1;
    return 0;
}
