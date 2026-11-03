int main()
{
    int target = 7;
    int *ptr = &target;
    bool is_null = (ptr == nullptr);
    return is_null ? 1 : 0;
}
