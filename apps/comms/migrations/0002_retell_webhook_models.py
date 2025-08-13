# Generated manually to extend Communication and add CommsMessage/CommsEvent
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('comms', '0001_initial'),
    ]

    def gen_uids(apps, schema_editor):
        Communication = apps.get_model('comms', 'Communication')
        import uuid as _uuid
        for row in Communication.objects.all():
            # Only set if missing (new column will be NULL initially)
            if getattr(row, 'uid', None) is None:
                row.uid = _uuid.uuid4()
                row.save(update_fields=['uid'])

    operations = [
        # Step 1: add nullable uid without unique/default (SQLite safe)
        migrations.AddField(
            model_name='communication',
            name='uid',
            field=models.UUIDField(null=True, editable=False, db_index=True),
        ),
        # Step 2: backfill with per-row UUIDs
        migrations.RunPython(gen_uids, migrations.RunPython.noop),
        # Step 3: enforce unique + not null and set default for future rows
        migrations.AlterField(
            model_name='communication',
            name='uid',
            field=models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True),
        ),
        migrations.AddField(
            model_name='communication',
            name='channel',
            field=models.CharField(choices=[('web', 'Web'), ('phone', 'Phone'), ('whatsapp', 'WhatsApp'), ('chat', 'Chat')], default='chat', max_length=16),
        ),
        migrations.AddField(
            model_name='communication',
            name='conversation_id',
            field=models.CharField(blank=True, default='', db_index=True, max_length=128),
        ),
        migrations.AddField(
            model_name='communication',
            name='language',
            field=models.CharField(default='es', max_length=16),
        ),
        migrations.AddField(
            model_name='communication',
            name='tokens',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='communication',
            name='source',
            field=models.CharField(default='retell', max_length=32),
        ),
        migrations.AlterField(
            model_name='communication',
            name='summary',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddIndex(
            model_name='communication',
            index=models.Index(fields=['conversation_id'], name='comms_commu_conversa_idx'),
        ),
        migrations.AddIndex(
            model_name='communication',
            index=models.Index(fields=['agent_id'], name='comms_commu_agent_id_idx'),
        ),
        migrations.CreateModel(
            name='CommsMessage',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('message_id', models.CharField(db_index=True, max_length=128)),
                ('role', models.CharField(max_length=16)),
                ('text', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('nlp', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('communication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='comms.communication')),
            ],
            options={'ordering': ('timestamp', 'created_at')},
        ),
        migrations.CreateModel(
            name='CommsEvent',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('event_type', models.CharField(max_length=64)),
                ('payload', models.JSONField(blank=True, default=dict)),
                ('idempotency_key', models.CharField(db_index=True, max_length=255, unique=True)),
                ('trace_id', models.CharField(blank=True, max_length=128, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('communication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='events', to='comms.communication')),
            ],
            options={'ordering': ('created_at',)},
        ),
    ]
