class Counter
{
public:
    int next()
    {
        ++value_;
        return value_;
    }

private:
    int value_ = 0;
};

int main()
{
    Counter counter;
    (void)counter.next();
    return 0;
}
