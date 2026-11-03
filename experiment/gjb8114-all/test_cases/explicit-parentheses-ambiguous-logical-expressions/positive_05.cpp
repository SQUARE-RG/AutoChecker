int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    bool result = ((a && b) || (c && d));
    return result ? 0 : 1;
}
