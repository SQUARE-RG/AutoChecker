int main()
{
    int* p = new int(5);
    int before = *p;

    delete p;
    p = new int(7);

    int after = *p;
    delete p;

    return before + after;
}
