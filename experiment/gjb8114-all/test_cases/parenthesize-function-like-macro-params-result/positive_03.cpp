#define ADD(a, b) ((a) + (b))

int main()
{
    int x = 10;
    int y = 20;
    int sum = ADD(x + 1, y - 1);
    return sum == 30 ? 0 : 1;
}
