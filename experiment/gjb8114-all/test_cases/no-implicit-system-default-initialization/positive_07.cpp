// positive_07.cpp
struct CounterStore
{
    inline static int counters[4] = {0, 0, 0, 0};

    static int total()
    {
        int sum = 0;
        for (int i = 0; i < 4; ++i)
        {
            sum += counters[i];
        }
        return sum;
    }
};

int main()
{
    CounterStore::counters[0] = 1;
    return CounterStore::total();
}
