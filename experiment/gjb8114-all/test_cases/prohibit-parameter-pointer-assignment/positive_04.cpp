int read_const_pointer_parameter(const int* p)
{
    return *p;
}

int main()
{
    int data = 5;
    return read_const_pointer_parameter(&data);
}
