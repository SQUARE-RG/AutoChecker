struct Data
{
    signed flag : 2;
    signed other : 3;
};

int main()
{
    Data d{};
    d.flag = -1;
    d.other = -1;
    return 0;
}
