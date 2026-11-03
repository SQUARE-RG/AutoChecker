int main()
{
    int target = 0;
    int* ptr = &target;
    float value = -2.5f;
    *ptr = static_cast<int>(value);
    return target;
}
