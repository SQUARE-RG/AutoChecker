long combine(int left, long right = 2L);

long combine(int left, long right)
{
    return static_cast<long>(left) + right;
}

int main()
{
    return combine(1) == 3 ? 0 : 1;
}
