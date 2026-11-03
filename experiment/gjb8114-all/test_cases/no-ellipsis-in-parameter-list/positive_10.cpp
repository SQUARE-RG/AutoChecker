int call_fixed(int (*cb)(int, int), int a, int b) {
    return cb(a, b);
}

int main()
{
    return 0;
}
