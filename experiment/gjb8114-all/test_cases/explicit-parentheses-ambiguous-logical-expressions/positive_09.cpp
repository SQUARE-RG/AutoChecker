bool evaluate(bool a, bool b, bool c, bool d)
{
    return ((a && b) || (c || d));
}

int main()
{
    bool a = true;
    bool b = false;
    bool c = true;
    bool d = false;
    bool result = evaluate(a, b, c, d);
    return result ? 0 : 1;
}
