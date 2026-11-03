int* pick_pointer(int* first, int* second, bool use_first)
{
    return use_first ? first : second;
}

int main()
{
    int a = 1;
    int b = 2;
    int* selected = pick_pointer(&a, &b, true);
    (void)selected;
    return 0;
}
