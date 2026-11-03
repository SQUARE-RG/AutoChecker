int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    if (((a || (b && c)) || d))
    {
        return 0;
    }
    return 1;
}
