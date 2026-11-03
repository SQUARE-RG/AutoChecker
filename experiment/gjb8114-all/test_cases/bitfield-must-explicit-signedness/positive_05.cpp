struct Counter
{
    signed long long ticks : 16;
    unsigned long long limit : 16;
    int id;
};

int main()
{
    Counter c;
    c.ticks = -100;
    c.limit = 50;
    c.id = 1;
    return 0;
}
