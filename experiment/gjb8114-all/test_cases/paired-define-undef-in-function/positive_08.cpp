static int add_with_local_macro(int left, int right)
{
#define LOCAL_ADD(a, b) ((a) + (b))
    int result = LOCAL_ADD(left, right);
#undef LOCAL_ADD
    return result;
}

int main()
{
    return add_with_local_macro(1, 2);
}
