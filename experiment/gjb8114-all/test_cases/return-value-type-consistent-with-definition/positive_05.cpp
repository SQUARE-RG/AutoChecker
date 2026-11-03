unsigned long compute(unsigned long input);

int main()
{
    unsigned long x = compute(10UL);
    return static_cast<int>(x);
}

unsigned long compute(unsigned long input)
{
    unsigned long temp = input * 2;
    return temp;
}
