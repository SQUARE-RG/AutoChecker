struct Matrix
{
    int rows;
    struct Cell
    {
        int value;
    } cells[4];
};

int main()
{
    Matrix matrix{};
    matrix.rows = 2;
    matrix.cells[0].value = 1;
    return 0;
}
