int main() {
    double dData = 0.0;
    double* pData = &dData;
    float fData;
    fData = static_cast<float>(*pData);
    return 0;
}
