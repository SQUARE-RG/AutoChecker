int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    int result = 0;
    if (a || (b && c))
    {
        result = 1;
    }
    else
    {
        result = 2;
    }
    return result;
}
