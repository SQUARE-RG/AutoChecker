using Count = unsigned int;

int main()
{
    int sum = 0;
    for (Count i = 0; i < 5; ++i)
    {
        sum += static_cast<int>(i);
    }
    return 0;
}
