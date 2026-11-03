int main()
{
    auto compare = [](bool a, bool b) { return a && !b; };
    bool result = compare(true, false);
    return result ? 1 : 0;
}
