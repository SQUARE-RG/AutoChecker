int main()
{
    int* p = nullptr;
    void* raw = &p;
    auto pp = static_cast<int**>(raw);
    (void)pp;
    return 0;
}
