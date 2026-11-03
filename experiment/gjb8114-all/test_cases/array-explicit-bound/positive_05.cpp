class sample
{
public:
    static constexpr int values[3] = {0, 1, 2};
};

int main()
{
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += sample::values[i];
    }
    return sum;
}
