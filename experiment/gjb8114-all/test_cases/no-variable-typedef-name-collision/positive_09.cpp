typedef unsigned long long Counter;

static Counter increment()
{
    static Counter total = 0;
    return total + 1;
}

int main()
{
    return static_cast<int>(increment());
}
