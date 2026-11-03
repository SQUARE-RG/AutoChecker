using Fn = int (*)(int, int);

int subtract(int a, int b) { return a - b; }

int main()
{
    Fn fp = static_cast<Fn>(&subtract);
    int result = fp(5, 3);
    return result == 2 ? 0 : 1;
}
