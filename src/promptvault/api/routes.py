"""API endpoint routes for PromptVault REST API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from promptvault.api.schemas import (
    DatasetCreate,
    EvaluationRunRequest,
    PromptCreate,
    RollbackRequest,
)
from promptvault.core.evaluation import EvaluationEngine
from promptvault.core.versioning import VersioningEngine
from promptvault.db import crud
from promptvault.db.engine import get_db

router = APIRouter()


# --- Prompt Endpoints ---


@router.post("/prompts")
def create_prompt(request: PromptCreate, db: Session = Depends(get_db)):
    """Create a new prompt with initial version."""
    try:
        engine = VersioningEngine(db)
        prompt, version = engine.create_prompt(
            name=request.name,
            content=request.content,
            description=request.description,
            variables=request.variables,
            model_config=request.llm_config,
            commit_message=request.commit_message,
            tags=request.tags,
        )
        return {
            "id": prompt.id,
            "name": prompt.name,
            "description": prompt.description,
            "tags": prompt.tags or [],
            "current_version_id": prompt.current_version_id,
            "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
            "updated_at": prompt.updated_at.isoformat() if prompt.updated_at else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/prompts")
def list_prompts(tags: str = None, limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """List all prompts."""
    tags_list = [t.strip() for t in tags.split(",")] if tags else None
    engine = VersioningEngine(db)
    prompts = engine.list_prompts(tags=tags_list, limit=limit, offset=offset)
    return [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "tags": p.tags or [],
            "created_at": p.created_at.isoformat() if p.created_at else None,
        }
        for p in prompts
    ]


@router.get("/prompts/{name}")
def get_prompt(name: str, db: Session = Depends(get_db)):
    """Get prompt latest version."""
    engine = VersioningEngine(db)
    prompt = engine.get_prompt(name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")

    version = engine.get_version(name)
    if not version:
        raise HTTPException(status_code=404, detail="No versions found")

    return {
        "id": prompt.id,
        "name": prompt.name,
        "description": prompt.description,
        "tags": prompt.tags or [],
        "current_version": {
            "version": version.version_number,
            "content": version.content,
            "variables": version.variables,
            "model_config": version.model_config,
        },
        "created_at": prompt.created_at.isoformat() if prompt.created_at else None,
    }


@router.get("/prompts/{name}/versions")
def list_versions(name: str, db: Session = Depends(get_db)):
    """List all versions of a prompt."""
    engine = VersioningEngine(db)
    prompt = engine.get_prompt(name)
    if not prompt:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")

    versions = engine.list_versions(name)
    return [
        {
            "id": v.id,
            "version": v.version_number,
            "content": v.content,
            "commit_message": v.commit_message,
            "created_at": v.created_at.isoformat() if v.created_at else None,
        }
        for v in versions
    ]


@router.get("/prompts/{name}/versions/{version}")
def get_version(name: str, version: int, db: Session = Depends(get_db)):
    """Get specific version of a prompt."""
    engine = VersioningEngine(db)
    pv = engine.get_version(name, version)
    if not pv:
        raise HTTPException(status_code=404, detail=f"Version {version} not found")

    return {
        "id": pv.id,
        "prompt_id": pv.prompt_id,
        "version": pv.version_number,
        "content": pv.content,
        "variables": pv.variables,
        "model_config": pv.model_config,
        "commit_message": pv.commit_message,
        "created_at": pv.created_at.isoformat() if pv.created_at else None,
    }


@router.post("/prompts/{name}/rollback")
def rollback_prompt(name: str, request: RollbackRequest, db: Session = Depends(get_db)):
    """Rollback to a previous prompt version."""
    try:
        engine = VersioningEngine(db)
        new_version = engine.rollback(
            name, request.version, request.commit_message
        )
        return {
            "id": new_version.id,
            "prompt_id": new_version.prompt_id,
            "version": new_version.version_number,
            "commit_message": new_version.commit_message,
            "created_at": new_version.created_at.isoformat()
            if new_version.created_at
            else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


# --- Dataset Endpoints ---


@router.post("/datasets")
def create_dataset(request: DatasetCreate, db: Session = Depends(get_db)):
    """Create a new dataset."""
    try:
        dataset = crud.create_dataset(
            db,
            name=request.name,
            description=request.description,
            items=request.items,
        )
        return {
            "id": dataset.id,
            "name": dataset.name,
            "description": dataset.description,
            "items_count": len(dataset.items),
            "created_at": dataset.created_at.isoformat()
            if dataset.created_at
            else None,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/datasets")
def list_datasets(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """List all datasets."""
    datasets = crud.list_datasets(db, limit=limit, offset=offset)
    return [
        {
            "id": d.id,
            "name": d.name,
            "description": d.description,
            "items_count": len(d.items),
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in datasets
    ]


@router.get("/datasets/{name}")
def get_dataset(name: str, db: Session = Depends(get_db)):
    """Get a dataset with items."""
    dataset = crud.get_dataset(db, name)
    if not dataset:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    return {
        "id": dataset.id,
        "name": dataset.name,
        "description": dataset.description,
        "items": [
            {
                "id": item.id,
                "input": item.input,
                "expected_output": item.expected_output,
            }
            for item in dataset.items
        ],
        "created_at": dataset.created_at.isoformat()
        if dataset.created_at
        else None,
    }


# --- Evaluation Endpoints ---


@router.post("/evaluations")
def run_evaluation(request: EvaluationRunRequest, db: Session = Depends(get_db)):
    """Run evaluation of a prompt version against a dataset."""
    try:
        engine = EvaluationEngine(db)
        eval_id = engine.run_evaluation(
            prompt_name=request.prompt_name,
            dataset_name=request.dataset_name,
            version=request.version,
            model_config=request.llm_config,
        )
        evaluation = crud.get_evaluation(db, eval_id)
        return {
            "id": evaluation.id,
            "status": evaluation.status,
            "model_config": evaluation.model_config,
            "created_at": evaluation.created_at.isoformat()
            if evaluation.created_at
            else None,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/evaluations/{evaluation_id}")
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    """Get evaluation status."""
    evaluation = crud.get_evaluation(db, evaluation_id)
    if not evaluation:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return {
        "id": evaluation.id,
        "status": evaluation.status,
        "model_config": evaluation.model_config,
        "metrics": evaluation.metrics,
        "created_at": evaluation.created_at.isoformat()
        if evaluation.created_at
        else None,
        "completed_at": evaluation.completed_at.isoformat()
        if evaluation.completed_at
        else None,
    }


@router.get("/evaluations/{evaluation_id}/report")
def get_evaluation_report(evaluation_id: str, db: Session = Depends(get_db)):
    """Get evaluation report with results."""
    engine = EvaluationEngine(db)
    report = engine.get_report(evaluation_id)
    if not report:
        raise HTTPException(status_code=404, detail="Evaluation not found")
    return report
