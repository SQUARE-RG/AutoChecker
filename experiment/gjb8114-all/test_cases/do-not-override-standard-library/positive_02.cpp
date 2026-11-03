namespace mylib
{
    int strxfrm(int a, int b)
    {
        return ((a > b) ? a : b);
    }
}

int main()
{
    int ret;
    ret = mylib::strxfrm(2, 3);
    return ret;
}
