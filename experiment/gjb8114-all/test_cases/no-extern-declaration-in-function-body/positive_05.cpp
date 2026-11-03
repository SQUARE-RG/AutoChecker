// positive_05.cpp
int g_value = 10;
int* g_ptr = &g_value;

int read_ptr_value()
{
    return *g_ptr;
}

int main()
{
    return read_ptr_value();
}
