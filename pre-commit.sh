echo "________________ black          ________________________________________________"
black . -l 1000
echo ""

echo "________________ flake8         ________________________________________________"
flake8 --ignore=E501
echo ""

echo "________________ pytest         ________________________________________________"
pytest --cov-report html --cov tempo
echo ""

echo "________________ git            ________________________________________________"
git add .
git status
echo ""

