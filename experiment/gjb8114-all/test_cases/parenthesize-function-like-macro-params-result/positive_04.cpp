#define LOW_BIT(x) ((x) | 1)

int main()
{
    int value = 2;
    bool result = (LOW_BIT(value) == 0);
    return result ? 0 : 1;
}
