# AIMED Agent Swarm - Makefile
# 快速命令参考

.PHONY: help install dev test lint clean run docker-build docker-up docker-down

# 默认目标
help:
	@echo "AIMED Agent Swarm - 快速命令"
	@echo ""
	@echo "开发环境:"
	@echo "  make install      安装生产依赖"
	@echo "  make dev          安装开发依赖"
	@echo "  make run          启动开发服务器"
	@echo ""
	@echo "测试:"
	@echo "  make test         运行所有测试"
	@echo "  make test-verbose 运行测试（详细输出）"
	@echo "  make coverage     生成测试覆盖率报告"
	@echo ""
	@echo "代码质量:"
	@echo "  make lint         运行代码检查"
	@echo "  make format       格式化代码"
	@echo "  make security     安全扫描"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build 构建 Docker 镜像"
	@echo "  make docker-up    启动 Docker 服务"
	@echo "  make docker-down  停止 Docker 服务"
	@echo "  make docker-logs  查看 Docker 日志"
	@echo ""
	@echo "清理:"
	@echo "  make clean        清理临时文件"
	@echo ""

# 安装依赖
install:
	pip install -r requirements.txt

dev: install
	pip install pytest-cov bandit black flake8

# 运行服务器
run:
	uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 测试
test:
	pytest tests/ -v

test-verbose:
	pytest tests/ -v -s

coverage:
	pytest tests/ --cov=agents --cov=routers --cov=main --cov=config --cov-report=html --cov-report=term-missing
	@echo "覆盖率报告已生成：htmlcov/index.html"

# 代码质量
lint:
	flake8 agents/ routers/ main.py config.py --max-line-length=100 --ignore=E501,W503

format:
	black agents/ routers/ main.py config.py --line-length 100

security:
	bandit -r agents/ routers/ -f json -o bandit-report.json
	@echo "安全扫描完成：bandit-report.json"

# Docker
docker-build:
	docker-compose -f deploy/docker-compose.yml build

docker-up:
	docker-compose -f deploy/docker-compose.yml up -d

docker-down:
	docker-compose -f deploy/docker-compose.yml down

docker-logs:
	docker-compose -f deploy/docker-compose.yml logs -f

# 清理
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
	rm -rf dist/ build/ *.egg-info
	@echo "清理完成"

# 数据库迁移（预留）
migrate:
	@echo "数据库迁移功能待实现"

# 初始化项目
init:
	cp .env.example .env
	@echo "项目初始化完成，请编辑 .env 文件配置环境变量"
