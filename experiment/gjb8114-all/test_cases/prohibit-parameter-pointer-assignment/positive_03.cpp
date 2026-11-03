static int global_value = 7;

int read_through_local_copy(int* p)
{
    int* local = p;
    local = &global_value;
    return *local;
}

int main()
{
    int data = 3;
    return read_through_local_copy(&data);
}
