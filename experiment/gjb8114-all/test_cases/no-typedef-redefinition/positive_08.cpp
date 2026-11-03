typedef int GlobalInt;

union Storage
{
    typedef double RealPartType;
    GlobalInt integerPart;
    RealPartType realPart;
};

int main()
{
    Storage s;
    s.integerPart = 1;
    s.realPart = 2.5;
    return 0;
}
