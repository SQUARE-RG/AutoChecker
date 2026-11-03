using Fn = int (*)(int, int);

int subtract(int a, int b) { return a - b; }

int main()
{
    Fn* fp = new Fn(&subtract);
    int result = (*fp)(5, 3);
    delete fp;
    return result == 2 ? 0 : 1;
}
