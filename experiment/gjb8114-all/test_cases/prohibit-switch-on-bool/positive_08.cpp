int main()
{
    long long n = 3;
    int code = 0;
    switch (n) {
        case 0:
            code = 10;
            break;
        case 1:
            code = 20;
            break;
        default:
            code = 30;
            break;
    }
    return code;
}
